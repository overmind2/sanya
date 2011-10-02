function main()
    local add, sum1

    add = function (a, b)
        return a + b
    end

    sum1 = function (n, accu)
        if 0 < n then
            return sum1(add(n, -2), add(add(accu, n), add(n, -1)))
        else
            return accu
        end
    end

    print(sum1(10000000, 0))
end

main()

